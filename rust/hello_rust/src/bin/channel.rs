#![allow(unused)]
use std::sync::mpsc;
use std::sync::mpsc::{Receiver, Sender};
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel::<String>();

    {
        for i in 0..10 {
            let txc = tx.clone();
            thread::spawn(move || {
                txc.send(format!("Hello {i}")).unwrap();
            });
        }
        drop(tx);
    }

    for e in rx {
        println!("e: {e}");
    }
}
