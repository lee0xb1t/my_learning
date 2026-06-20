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




/* ================================================================== */
// Global variables
/* ================================================================== */

UINT64 insCount    = 0; //number of dynamically executed instructions
UINT64 bblCount    = 0; //number of dynamically executed basic blocks
UINT64 threadCount = 0; //total number of threads, including main thread
ADDRINT MainModuleAddress = 0;

std::ostream* out = &std::cerr;

/* ===================================================================== */
// Command line switches
/* ===================================================================== */
KNOB< std::string > KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool", "o", "", "specify file name for MyPinTool output");

KNOB< BOOL > KnobCount(KNOB_MODE_WRITEONCE, "pintool", "count", "1",
                       "count instructions, basic blocks and threads in the application");

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

    *out << "ADDR:" << CurrentAddr << ",numInst:" << numInstInBbl << ",branch_target:" << branch_target << "\n";
}

VOID AfterBbl(UINT32 numInstInBbl)
{
    bblCount++;
    insCount += numInstInBbl;
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
    for (BBL bbl = TRACE_BblHead(trace); BBL_Valid(bbl); bbl = BBL_Next(bbl))
    {
        ADDRINT bbl_addr = BBL_Address(bbl);
        if (IsMainModuleAddr(bbl_addr)) {
            //BBL_InsertCall(bbl, IPOINT_BEFORE, (AFUNPTR)BeforeBbl, IARG_ADDRINT, BBL_Address(bbl), IARG_UINT32, BBL_NumIns(bbl), IARG_BRANCH_TARGET_ADDR, IARG_END);
            INS last_ins = BBL_InsTail(bbl);
            if (INS_IsControlFlow(last_ins) || INS_IsCall(last_ins)) {
                INS_InsertCall(last_ins, IPOINT_BEFORE, (AFUNPTR)BeforeBbl, IARG_ADDRINT, BBL_Address(bbl), IARG_UINT32, BBL_NumIns(bbl), IARG_BRANCH_TARGET_ADDR, IARG_END);
            }
        }
    }
}

/*!
 * Increase counter of threads in the application.
 * This function is called for every thread created by the application when it is
 * about to start running (including the root thread).
 * @param[in]   threadIndex     ID assigned by PIN to the new thread
 * @param[in]   ctxt            initial register state for the new thread
 * @param[in]   flags           thread creation flags (OS specific)
 * @param[in]   v               value specified by the tool in the 
 *                              PIN_AddThreadStartFunction function call
 */
VOID ThreadStart(THREADID threadIndex, CONTEXT* ctxt, INT32 flags, VOID* v) { threadCount++; }

VOID ImageLoad(IMG img, VOID* ctx) {
    if (IMG_IsMainExecutable(img)) {
        MainModuleAddress = IMG_StartAddress(img);
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
    *out << "===============================================" << std::endl;
    *out << "VMP Pin Tool analysis results: " << std::endl;
    *out << "Number of instructions: " << insCount << std::endl;
    *out << "Number of basic blocks: " << bblCount << std::endl;
    *out << "Number of threads: " << threadCount << std::endl;
    *out << "Address of main module: 0x" << std::hex << MainModuleAddress << std::endl;
    *out << "===============================================" << std::endl;
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
    } else {
        std::cerr << "No input file!" << std::endl;
        return Usage();
    }

    if (KnobCount)
    {
        // Register function to be called to instrument traces
        TRACE_AddInstrumentFunction(Trace, 0);

        // Register function to be called for every thread before it starts running
        PIN_AddThreadStartFunction(ThreadStart, 0);

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
