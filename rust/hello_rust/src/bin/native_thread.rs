#![allow(unused)]

use std::thread::{self};

use tokio::task::JoinHandle;
use tokio::time::Duration;

#[tokio::main]
async fn main() {
    let mut handles: Vec<JoinHandle<()>> = vec![];
    for i in 0..1000000 {
        let h = tokio::spawn(async move {
            tokio::time::sleep(Duration::from_millis(1000));
            println!("{i}");
        });
        handles.push(h);
    }

    for h in handles {
        //h.await.unwrap();
        h.await.unwrap();
    }
}
