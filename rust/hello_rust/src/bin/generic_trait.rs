#![allow(unused)]

trait List<T> {
    fn count(&self) -> usize;
    fn first(&self) -> &T;
}

impl List<i32> for (i32, i32) {
    fn count(&self) -> usize {
        2
    }

    fn first(&self) -> &i32 {
        &self.0
    }
}

impl<T> List<T> for Vec<T> {
    fn count(&self) -> usize {
        self.len()
    }

    fn first(&self) -> &T {
        &self[0]
    }
}

impl<A, B> List<(A, B)> for [(A, B); 2] {
    fn count(&self) -> usize {
        2
    }

    fn first(&self) -> &(A, B) {
        &self[0]
    }
}

fn main() {
    let t = (1i32, 2i32);
    println!("t.count: {}", t.count());
    println!("t.first: {}", t.first());

    let v = vec![1.0, 2.0, 3.0];
    println!("v.count: {}", v.count());
    println!("v.first: {}", v.first());

    let a = [(1, "hello"), (2, "rust")];
    println!("a.count: {}", a.count());
    println!("a.first: {:?}", a.first());
}
