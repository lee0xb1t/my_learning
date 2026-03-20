#![allow(unused)]

struct ArrayIter<T> {
    data: [T; 10],
    cursor: usize,
}

trait GenericIterator<T> {
    fn next(&mut self) -> Option<T>;
}

impl GenericIterator<i32> for ArrayIter<i32> {
    fn next(&mut self) -> Option<i32> {
        match self.data.get(self.cursor) {
            Some(v) => {
                self.cursor += 1;
                Some(*v)
            }
            _ => None,
        }
    }
}

// 问题：i32类型拥有bool类型的迭代函数
impl GenericIterator<bool> for ArrayIter<i32> {
    fn next(&mut self) -> Option<bool> {
        Some(true)
    }
}

trait GenericIteratorAssoc {
    type TYPE;
    fn get_next(&mut self) -> Option<Self::TYPE>;
}

impl GenericIteratorAssoc for ArrayIter<i32> {
    type TYPE = i32;
    fn get_next(&mut self) -> Option<Self::TYPE> {
        match self.data.get(self.cursor) {
            Some(v) => {
                self.cursor += 1;
                Some(*v)
            }
            _ => None,
        }
    }
}

fn main() {
    let mut a = ArrayIter {
        data: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        cursor: 0,
    };
    while let Some(v) = a.get_next() {
        println!("next: {v}");
    }
}
