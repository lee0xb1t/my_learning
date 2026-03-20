#![allow(unused)]
use std::thread;
use std::thread::JoinHandle;
use std::time::Duration;

fn main() {
    let t1: JoinHandle<()> = thread::spawn(|| {
        for i in 0..5 {
            thread::sleep(Duration::from_millis(500));
            println!("t1 i: {i}");
        }
    });

    let t2: JoinHandle<()> = thread::spawn(|| {
        for i in 0..5 {
            thread::sleep(Duration::from_millis(500));
            println!("t1 i: {i}");
        }
    });

    t1.join().unwrap();
    t2.join().unwrap();

    let v = 100;
    let t: JoinHandle<i32> = thread::spawn(move || {
        let mut i = 0;
        for x in 1..=v {
            i += x;
        }
        i
    });

    match t.join() {
        Ok(v) => println!("thread result: {v}"),
        Err(e) => println!("thread error: {}", v),
    }
}
