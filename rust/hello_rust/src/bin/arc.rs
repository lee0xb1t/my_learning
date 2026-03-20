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
    let counter = Arc::new(i);

    let c1 = Arc::clone(&counter);
    let t1 = thread::spawn(move || {
        let mut g: MutexGuard<'_, i32> = c1.lock().unwrap();
        *g += 1;
    });

    let c2 = Arc::clone(&counter);
    let t2 = thread::spawn(move || {
        let mut g: MutexGuard<'_, i32> = c2.lock().unwrap();
        *g += 1;
    });

    t1.join().unwrap();
    t2.join().unwrap();

    // thread::scope(|s| {
    //     s.spawn(|| {
    //         let l = i.lock();
    //         let mut g: MutexGuard<'_, i32> = l.unwrap();
    //         // panic!("t1 is panic");
    //         *g+=1;
    //     });

    //     s.spawn(|| {
    //         let mut g: MutexGuard<'_, i32> = i.lock().unwrap();
    //         *g+=1;
    //     });
    // });

    {
        let s = counter.lock().unwrap();
        println!("i: {:?}", s);
    }

    let s = counter.lock().unwrap();
    println!("i: {:?}", s);
}
