from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Iterator, Tuple
import json

@dataclass
class MemoryAccess:
    """单次内存访问记录"""
    addr: str          # 十六进制地址 (如 "0x76fac4")
    val: str           # 十六进制值 (如 "0xc41015")
    size: int          # 访问大小 (字节)
    
    def addr_int(self) -> int:
        return int(self.addr, 16)
    
    def val_int(self) -> int:
        return int(self.val, 16)

@dataclass
class Registers:
    """CPU 寄存器状态快照"""
    eax: str = "0x0"
    ecx: str = "0x0"
    edx: str = "0x0"
    ebx: str = "0x0"
    esp: str = "0x0"
    ebp: str = "0x0"
    esi: str = "0x0"
    edi: str = "0x0"
    eflags: str = "0x0"
    
    def to_int_dict(self) -> Dict[str, int]:
        """返回所有寄存器的整数值字典"""
        return {k: int(v, 16) for k, v in self.__dict__.items()}
    
    def get(self, name: str) -> int:
        """获取指定寄存器的整数值"""
        if hasattr(self, name):
            return int(getattr(self, name), 16)
        raise KeyError(f"Unknown register: {name}")

@dataclass
class InstructionSnapshot:
    """单条指令的执行快照"""
    addr: str                     # 指令地址
    size: int                     # 指令长度 (字节)
    opcodes: List[str]            # 操作码字节列表 (如 ['c3'])
    mems: List[MemoryAccess]      # 内存访问记录
    regs: Registers               # 寄存器状态
    
    def addr_int(self) -> int:
        return int(self.addr, 16)
    
    def opcode_bytes(self) -> bytes:
        """将操作码列表转为字节串"""
        return bytes([int(b, 16) for b in self.opcodes])
    
    @classmethod
    def from_dict(cls, data: dict) -> "InstructionSnapshot":
        """从原始字典构建实例"""
        return cls(
            addr=data['addr'],
            size=data['size'],
            opcodes=data['opcodes'],
            mems=[MemoryAccess(**m) for m in data.get('mems', [])],
            regs=Registers(**data['regs'])
        )
    
    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            'addr': self.addr,
            'size': self.size,
            'opcodes': self.opcodes,
            'mems': [{'addr': m.addr, 'val': m.val, 'size': m.size} for m in self.mems],
            'regs': self.regs.__dict__.copy()
        }

@dataclass
class TraceIndex:
    """轨迹索引容器，按序号存储多个指令快照"""
    snapshots: Dict[int, InstructionSnapshot] = field(default_factory=dict)
    
    def add(self, index: int, snapshot: InstructionSnapshot) -> None:
        self.snapshots[index] = snapshot
    
    def get(self, index: int) -> Optional[InstructionSnapshot]:
        return self.snapshots.get(index)
    
    def get_all(self) -> List[InstructionSnapshot]:
        return [self.snapshots[i] for i in self.snapshots.keys()]
    
    def filter_by_opcode(self, opcode: str) -> List[InstructionSnapshot]:
        """筛选包含指定操作码的指令"""
        return [s for s in self.get_all() if opcode in s.opcodes]
    
    @classmethod
    def from_dict(cls, data: Dict[int, dict]) -> "TraceIndex":
        """从原始字典构建"""
        index = cls()
        for idx, snapshot_data in data.items():
            snapshot = InstructionSnapshot.from_dict(snapshot_data)
            index.add(idx, snapshot)
        return index
    
    def to_dict(self) -> Dict[int, dict]:
        """序列化为字典"""
        return {idx: s.to_dict() for idx, s in self.snapshots.items()}
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_json(cls, json_str: str) -> "TraceIndex":
        data = json.loads(json_str)
        return cls.from_dict({int(k): v for k, v in data.items()})
    
    # ========== 新增遍历函数 ==========
    
    # ---------- 基础遍历 ----------
    def iter_items(self) -> Iterator[Tuple[int, InstructionSnapshot]]:
        for idx in self.snapshots.keys():
            yield idx, self.snapshots[idx]
    
    def iter_snapshots_sort(self) -> Iterator[InstructionSnapshot]:
        """按序号升序遍历所有快照"""
        for idx in sorted(self.snapshots.keys()):
            yield self.snapshots[idx]
    
    def iter_reverse(self) -> Iterator[Tuple[int, InstructionSnapshot]]:
        """按序号降序遍历所有条目"""
        for idx in sorted(self.snapshots.keys(), reverse=True):
            yield idx, self.snapshots[idx]
    
    # ---------- 条件遍历 ----------
    def iter_where(self, predicate: Callable[[InstructionSnapshot], bool]) -> Iterator[InstructionSnapshot]:
        """遍历满足条件的快照"""
        for snapshot in self.iter_snapshots_sort():
            if predicate(snapshot):
                yield snapshot
    
    def iter_where_with_idx(self, predicate: Callable[[int, InstructionSnapshot], bool]) -> Iterator[Tuple[int, InstructionSnapshot]]:
        """遍历满足条件 (索引和快照) 的条目"""
        for idx, snapshot in self.iter_items():
            if predicate(idx, snapshot):
                yield idx, snapshot
    
    def iter_filter_by_addr(self, addr: str) -> Iterator[InstructionSnapshot]:
        """遍历指定地址的指令"""
        return self.iter_where(lambda s: s.addr == addr)
    
    def iter_filter_by_memory(self, mem_addr: str) -> Iterator[InstructionSnapshot]:
        """遍历访问了指定内存地址的指令"""
        def predicate(s: InstructionSnapshot) -> bool:
            return any(m.addr == mem_addr for m in s.mems)
        return self.iter_where(predicate)
    
    def iter_filter_by_register(self, reg_name: str, value: str) -> Iterator[InstructionSnapshot]:
        """遍历指定寄存器等于某值的指令"""
        def predicate(s: InstructionSnapshot) -> bool:
            regs = s.regs.__dict__
            return reg_name in regs and regs[reg_name] == value
        return self.iter_where(predicate)
    
    # ---------- 窗口遍历 ----------
    def iter_window(self, start_idx: int, end_idx: int) -> Iterator[Tuple[int, InstructionSnapshot]]:
        """遍历指定索引范围内的条目 [start_idx, end_idx)"""
        for idx, snapshot in self.iter_items():
            if start_idx <= idx < end_idx:
                yield idx, snapshot
    
    def iter_chunk(self, chunk_size: int) -> Iterator[List[Tuple[int, InstructionSnapshot]]]:
        """按分块遍历，每次返回一个块（列表）"""
        items = list(self.iter_items())
        for i in range(0, len(items), chunk_size):
            yield items[i:i + chunk_size]
    
    def iter_group_by_addr(self) -> Dict[str, List[InstructionSnapshot]]:
        """按指令地址分组遍历，返回分组字典"""
        groups: Dict[str, List[InstructionSnapshot]] = {}
        for snapshot in self.iter_snapshots_sort():
            groups.setdefault(snapshot.addr, []).append(snapshot)
        return groups
    
    # ---------- 操作遍历 ----------
    def for_each(self, func: Callable[[InstructionSnapshot], None]) -> None:
        """对每个快照执行操作"""
        for snapshot in self.iter_snapshots_sort():
            func(snapshot)
    
    def map(self, func: Callable[[InstructionSnapshot], Any]) -> List[Any]:
        """对每个快照应用映射函数，返回结果列表"""
        return [func(s) for s in self.iter_snapshots_sort()]
    
    def reduce(self, func: Callable[[Any, InstructionSnapshot], Any], initial: Any) -> Any:
        """对快照序列进行归约"""
        result = initial
        for snapshot in self.iter_snapshots_sort():
            result = func(result, snapshot)
        return result
    
    def find(self, predicate: Callable[[InstructionSnapshot], bool]) -> Optional[InstructionSnapshot]:
        """查找第一个满足条件的快照"""
        for snapshot in self.iter_snapshots_sort():
            if predicate(snapshot):
                return snapshot
        return None
    
    def find_all(self, predicate: Callable[[InstructionSnapshot], bool]) -> List[InstructionSnapshot]:
        """查找所有满足条件的快照"""
        return list(self.iter_where(predicate))
    
    # ---------- 统计遍历 ----------
    def count(self) -> int:
        """返回快照总数"""
        return len(self.snapshots)
    
    def count_where(self, predicate: Callable[[InstructionSnapshot], bool]) -> int:
        """统计满足条件的快照数量"""
        return sum(1 for _ in self.iter_where(predicate))
    
    def count_by_opcode(self) -> Dict[str, int]:
        """统计每个操作码的出现次数"""
        result: Dict[str, int] = {}
        for snapshot in self.iter_snapshots_sort():
            for opcode in snapshot.opcodes:
                result[opcode] = result.get(opcode, 0) + 1
        return result
    
    def count_by_addr(self) -> Dict[str, int]:
        """统计每个地址的指令数量"""
        result: Dict[str, int] = {}
        for snapshot in self.iter_snapshots_sort():
            result[snapshot.addr] = result.get(snapshot.addr, 0) + 1
        return result