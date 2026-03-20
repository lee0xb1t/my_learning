#![allow(unused)]
use std::cell::RefCell;
use std::rc::{Rc, Weak};

#[derive(Debug)]
struct Node {
    value: i32,
    neighbors: RefCell<Vec<Weak<Node>>>,
}

fn main() {
    let node0 = Rc::new(Node {
        value: 0,
        neighbors: RefCell::new(vec![]),
    });

    let node1 = Rc::new(Node {
        value: 0,
        neighbors: RefCell::new(vec![]),
    });

    {
        let mut r0 = node0.neighbors.borrow_mut();
        r0.push(Rc::downgrade(&node1));

        let mut r1 = node1.neighbors.borrow_mut();
        r1.push(Rc::downgrade(&node0));
    }

    std::mem::drop(node1);

    println!("node0 strong count: {}", Rc::strong_count(&node0));
    // println!("node1 strong count: {}", Rc::strong_count(&node1));

    println!("node0: {:?}", node0);

    let binding = node0.neighbors.borrow();
    let old_node1 = binding.get(0).unwrap();
    if let Some(v) = old_node1.upgrade() {
        println!("node1 is not free");
    } else {
        println!("node1 is free");
    }

    println!("node0: {:?}", node0);

    // upgrade
    let s = Rc::new("Hello".to_string());

    let w = Rc::downgrade(&s);

    println!("s strong count: {}", Rc::strong_count(&s));
    {
        let strong = w.upgrade();
        if let Some(v) = w.upgrade() {
            println!("v: {}", v);
        }

        println!("s strong count: {}", Rc::strong_count(&s));
    }
    println!("s strong count: {}", Rc::strong_count(&s));
}
