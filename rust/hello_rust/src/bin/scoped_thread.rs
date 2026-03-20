#![allow(unused)]

use std::thread;

fn main() {
    let msg = "Hello".to_string();

    // auto join in scope
    let (a, b) = thread::scope(|scope| {
        let t1 = scope.spawn(|| {
            println!("msg: {}", msg);
            1
        });
        let t2 = scope.spawn(|| {
            println!("msg: {}", msg);
            2
        });

        (t1.join().unwrap(), t2.join().unwrap())
    });

    println!("{a}\n{b}\n{msg}");
}
