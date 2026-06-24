/*
 * Copyright (C) 2007-2023 Intel Corporation.
 * SPDX-License-Identifier: MIT
 */

 /*! @file
  *  This is an example of the PIN tool that demonstrates some basic PIN APIs
  *  and could serve as the starting point for developing your first PIN tool
  */

#include "pin.H"
#include <iostream>
#include <fstream>
#include <vector>



  /* ================================================================== */
  // Global variables
  /* ================================================================== */

UINT64 insCount = 0; //number of dynamically executed instructions
UINT64 bblCount = 0; //number of dynamically executed basic blocks
UINT64 threadCount = 0; //total number of threads, including main thread
ADDRINT MainModuleAddress = 0;

std::ostream* out = &std::cerr;

UINT32 StartAddrTrace = 0;
UINT32 EndAddrTrace = 0;
BOOL TraceEnable = FALSE;
UINT32 TraceCount = 0;

/* ===================================================================== */
// Command line switches
/* ===================================================================== */
KNOB< std::string > KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool", "o", "", "specify file name for MyPinTool output");

KNOB< BOOL > KnobCount(KNOB_MODE_WRITEONCE, "pintool", "count", "1",
    "count instructions, basic blocks and threads in the application");

KNOB< std::string > KnobStart(KNOB_MODE_WRITEONCE, "pintool", "start", "", "Start adddress of trace");
KNOB< std::string > KnobEnd(KNOB_MODE_WRITEONCE, "pintool", "end", "", "End adddress of trace");

/* ===================================================================== */
// Utilities
/* ===================================================================== */

/*!
 *  Print out help message.
 */
INT32 Usage()
{
    std::cerr << "This tool prints out the number of dynamically executed " << std::endl
        << "instructions, basic blocks and threads in the application." << std::endl
        << std::endl;

    std::cerr << KNOB_BASE::StringKnobSummary() << std::endl;

    return -1;
}


ADDRINT GetMainModuleAddr() {
    for (IMG img = APP_ImgHead(); IMG_Valid(img); img = IMG_Next(img)) {
        if (IMG_IsMainExecutable(img)) {
            return IMG_StartAddress(img);
        }
    }
    return 0;
}

BOOL IsMainModuleAddr(ADDRINT test_addr) {
    for (IMG img = APP_ImgHead(); IMG_Valid(img); img = IMG_Next(img)) {
        if (IMG_IsMainExecutable(img)) {

            SEC first_sec = IMG_SecHead(img);
            SEC last_sec = IMG_SecTail(img);

            ADDRINT start_addr = SEC_Address(first_sec);

            ADDRINT end_addr = SEC_Address(last_sec);
            USIZE end_size = SEC_Size(last_sec);
            end_addr += end_size;

            if (test_addr >= start_addr && test_addr < end_addr) {
                return TRUE;
            }
        }
    }
    return FALSE;
}

BOOL IsValidVmpAddr(BBL bbl, ADDRINT test_addr) {
    ADDRINT addr = BBL_Address(bbl);
    IMG img = IMG_FindByAddress(addr);
    for (SEC sec = IMG_SecHead(img); SEC_Valid(sec); sec = SEC_Next(sec)) {
        ADDRINT sec_addr = SEC_Address(sec);
        USIZE sec_size = SEC_Size(sec);
        std::string sec_name = SEC_Name(sec);
        if (sec_name.find("vmp") != std::string::npos) {
            bool isinsec = (test_addr >= sec_addr && test_addr < (sec_addr + sec_size));
            if (isinsec) {
                return TRUE;
            }
        }

    }
    return FALSE;
}


/* ===================================================================== */
// Analysis routines
/* ===================================================================== */

/*!
 * Increase counter of the executed basic blocks and instructions.
 * This function is called for every basic block when it is about to be executed.
 * @param[in]   numInstInBbl    number of instructions in the basic block
 * @note use atomic operations for multi-threaded applications
 */
VOID BeforeBbl(ADDRINT CurrentAddr, UINT32 numInstInBbl, ADDRINT branch_target)
{
    bblCount++;
    insCount += numInstInBbl;

    //*out << "ADDR:" << CurrentAddr << ",numInst:" << numInstInBbl << ",branch_target:" << branch_target << "\n";
}

VOID AfterBbl(UINT32 numInstInBbl)
{
    bblCount++;
    insCount += numInstInBbl;
}

VOID BeforeIns_RecordIns(CONTEXT* ctx, const unsigned char* ins_ptr, USIZE ptr_size) {
    *out << "^addr:" << "0x" << std::hex << (UINT64)ins_ptr << ",";

    *out << "size:" << std::dec << ptr_size << ",";

    *out << "opcodes:";
    for (int i = 0; i < ptr_size; i++) {
        *out << std::hex << std::setw(2) << std::setfill('0') << (int)(UINT8)ins_ptr[i] << " ";
    }

    *out << std::dec << "\n";

    std::vector<LEVEL_BASE::REG> regs;
    regs.push_back(LEVEL_BASE::REG_EAX);
    regs.push_back(LEVEL_BASE::REG_ECX);
    regs.push_back(LEVEL_BASE::REG_EDX);
    regs.push_back(LEVEL_BASE::REG_EBX);
    regs.push_back(LEVEL_BASE::REG_ESP);
    regs.push_back(LEVEL_BASE::REG_EBP);
    regs.push_back(LEVEL_BASE::REG_ESI);
    regs.push_back(LEVEL_BASE::REG_EDI);
    regs.push_back(LEVEL_BASE::REG_EFLAGS);

    *out << "*regs:" << std::hex;
    for (auto reg : regs) {
        UINT32 Val = 0;
        PIN_GetContextRegval(ctx, reg, (UINT8*)&Val);
        *out << "0x" << Val << "|";
    }

    *out << "\n";

}

VOID BeforeIns_RecordMemRead(ADDRINT mem_addr, USIZE mem_size) {
    *out << "*mem_addr:" << "0x" << std::hex << mem_addr << std::dec << ",";

    switch (mem_size) {
    case 1:
        *out << "mem_val:" << "0x" << std::hex << static_cast<int>(*reinterpret_cast<UINT8*>(mem_addr)) << std::dec << ",";
        break;
    case 2:
        *out << "mem_val:" << "0x" << std::hex << *reinterpret_cast<UINT16*>(mem_addr) << std::dec << ",";
        break;
    case 4:
        *out << "mem_val:" << "0x" << std::hex << *reinterpret_cast<UINT32*>(mem_addr) << std::dec << ",";
        break;
    case 8:
        *out << "mem_val:" << "0x" << std::hex << *reinterpret_cast<UINT64*>(mem_addr) << std::dec << ",";
        break;
    default:
        std::cerr << "Unknown memory size" << std::endl;
        exit(1);
    }

    *out << "mem_size:" << std::dec << mem_size;
    *out << "\n";
}

/* ===================================================================== */
// Instrumentation callbacks
/* ===================================================================== */

/*!
 * Insert call to the CountBbl() analysis routine before every basic block
 * of the trace.
 * This function is called every time a new trace is encountered.
 * @param[in]   trace    trace to be instrumented
 * @param[in]   v        value specified by the tool in the TRACE_AddInstrumentFunction
 *                       function call
 */

VOID Trace(TRACE trace, VOID* v)
{
    //for (BBL bbl = TRACE_BblHead(trace); BBL_Valid(bbl); bbl = BBL_Next(bbl))
    //{
    //    ADDRINT bbl_addr = BBL_Address(bbl);
    //    if (IsMainModuleAddr(bbl_addr) && IsValidVmpAddr(bbl, bbl_addr)) {
    //        //BBL_InsertCall(bbl, IPOINT_BEFORE, (AFUNPTR)BeforeBbl, IARG_ADDRINT, BBL_Address(bbl), IARG_UINT32, BBL_NumIns(bbl), IARG_BRANCH_TARGET_ADDR, IARG_END);
    //        INS last_ins = BBL_InsTail(bbl);
    //        if (INS_IsControlFlow(last_ins) || INS_IsCall(last_ins)) {
    //            INS_InsertCall(last_ins, IPOINT_BEFORE, (AFUNPTR)BeforeBbl, IARG_ADDRINT, BBL_Address(bbl), IARG_UINT32, BBL_NumIns(bbl), IARG_BRANCH_TARGET_ADDR, IARG_END);
    //        }
    //    }
    //}

    for (BBL bbl = TRACE_BblHead(trace); BBL_Valid(bbl); bbl = BBL_Next(bbl)) {
        for (INS ins = BBL_InsHead(bbl); INS_Valid(ins); ins = INS_Next(ins)) {

            if (!IsMainModuleAddr(INS_Address(ins))) {
                continue;
            }

            if (TraceEnable) {
                if (INS_Address(ins) == (GetMainModuleAddr() + EndAddrTrace)) {
                    if (StartAddrTrace != EndAddrTrace) {
                        TraceEnable = FALSE;
                    }
                    TraceCount++;
                    //*out << "------\n";
                }
            } else if (INS_Address(ins) == (GetMainModuleAddr() + StartAddrTrace)) {
                TraceEnable = TRUE;
                TraceCount++;
                //*out << "------\n";
            }

            if (!TraceEnable) {
                continue;
            }

            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)BeforeIns_RecordIns, IARG_CALL_ORDER, CALL_ORDER_FIRST, IARG_CONTEXT, IARG_INST_PTR, IARG_UINT32, INS_Size(ins), IARG_END);

            if (INS_IsMemoryRead(ins)) {
                INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)BeforeIns_RecordMemRead, IARG_CALL_ORDER, CALL_ORDER_FIRST + 1, IARG_MEMORYREAD_EA, IARG_MEMORYREAD_SIZE, IARG_END);

                if (INS_HasMemoryRead2(ins)) {
                    INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)BeforeIns_RecordMemRead, IARG_CALL_ORDER, CALL_ORDER_FIRST + 2, IARG_MEMORYREAD2_EA, IARG_MEMORYREAD_SIZE, IARG_END);
                }
            }

            //if (IsMainModuleAddr(bbl_addr) && IsValidVmpAddr(bbl, bbl_addr)) {
            //    //BBL_InsertCall(bbl, IPOINT_BEFORE, (AFUNPTR)BeforeBbl, IARG_ADDRINT, BBL_Address(bbl), IARG_UINT32, BBL_NumIns(bbl), IARG_BRANCH_TARGET_ADDR, IARG_END);
            //    INS last_ins = BBL_InsTail(bbl);
            //    if (INS_IsControlFlow(last_ins) || INS_IsCall(last_ins)) {
            //        INS_InsertCall(last_ins, IPOINT_BEFORE, (AFUNPTR)BeforeBbl, IARG_ADDRINT, BBL_Address(bbl), IARG_UINT32, BBL_NumIns(bbl), IARG_BRANCH_TARGET_ADDR, IARG_END);
            //    }
            //}
        }
    }
}

//VOID ThreadStart(THREADID threadIndex, CONTEXT* ctxt, INT32 flags, VOID* v) { threadCount++; }



VOID ImageLoad(IMG img, VOID* ctx) {
    if (IMG_IsMainExecutable(img)) {
        MainModuleAddress = IMG_StartAddress(img);
        *out << "Address of main module: 0x" << std::hex << MainModuleAddress << std::endl;
        *out << "===============================================" << std::endl;
    }
}

/*!
 * Print out analysis results.
 * This function is called when the application exits.
 * @param[in]   code            exit code of the application
 * @param[in]   v               value specified by the tool in the
 *                              PIN_AddFiniFunction function call
 */
VOID Fini(INT32 code, VOID* v)
{
    //*out << "===============================================" << std::endl;
    //*out << "VMP Pin Tool analysis results: " << std::endl;
    //*out << "Number of instructions: " << insCount << std::endl;
    //*out << "Number of basic blocks: " << bblCount << std::endl;
    //*out << "Number of threads: " << threadCount << std::endl;
    //*out << "===============================================" << std::endl;
    std::cout << "Number of TraceCount: " << TraceCount << std::endl;
    out->flush();
}

/*!
 * The main procedure of the tool.
 * This function is called when the application image is loaded but not yet started.
 * @param[in]   argc            total number of elements in the argv array
 * @param[in]   argv            array of command line arguments,
 *                              including pin -t <toolname> -- ...
 */
int main(int argc, char* argv[])
{
    // Initialize PIN library. Print help message if -h(elp) is specified
    // in the command line or the command line is invalid
    if (PIN_Init(argc, argv))
    {
        return Usage();
    }

    std::string fileName = KnobOutputFile.Value();

    if (!fileName.empty())
    {
        out = new std::ofstream(fileName.c_str());
    }
    else {
        std::cerr << "No input file!" << std::endl;
        return Usage();
    }

    if (KnobStart.Value().empty() || KnobEnd.Value().empty()) {
        std::cerr << "No start address or end address!" << std::endl;
        return Usage();
    }

    StartAddrTrace = Uint32FromString(KnobStart.Value());
    EndAddrTrace = Uint32FromString(KnobEnd.Value());

    printf("start: 0x%x, end: 0x%x\n", StartAddrTrace, EndAddrTrace);

    // uintptr_t address = strtoull("7FF6A4B800", nullptr, 16);

    if (KnobCount)
    {
        // Register function to be called to instrument traces
        TRACE_AddInstrumentFunction(Trace, 0);

        // Register function to be called for every thread before it starts running
        //PIN_AddThreadStartFunction(ThreadStart, 0);

        IMG_AddInstrumentFunction(ImageLoad, 0);

        // Register function to be called when the application exits
        PIN_AddFiniFunction(Fini, 0);
    }

    std::cerr << "===============================================" << std::endl;
    std::cerr << "This application is instrumented by MyPinTool" << std::endl;
    if (!KnobOutputFile.Value().empty())
    {
        std::cerr << "See file " << KnobOutputFile.Value() << " for analysis results" << std::endl;
    }
    std::cerr << "===============================================" << std::endl;

    // Start the program, never returns
    PIN_StartProgram();

    return 0;
}

/* ===================================================================== */
/* eof */
/* ===================================================================== */
