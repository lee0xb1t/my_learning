#![allow(unused)]
use std::cell::RefCell;
use std::rc::Rc;
use std::sync::{Arc, Mutex, MutexGuard};
use std::thread;

struct Node {
    data: i32,
    neighbors: RefCell<Vec<Rc<Node>>>,
}

struct MNode {
    data: i32,
    neighbors: Mutex<Vec<Arc<Node>>>,
}

fn main() {
    let i = Mutex::new(1);

    thread::scope(|s| {
        s.spawn(|| {
            let l = i.lock();
            let mut g: MutexGuard<'_, i32> = l.unwrap();
            // panic!("t1 is panic");
            *g += 1;
        });

        s.spawn(|| {
            let mut g: MutexGuard<'_, i32> = i.lock().unwrap();
            *g += 1;
        });
    });

    println!("i: {:?}", i);
}
