#![allow(unused)]
use std::cell::RefCell;
use std::rc::Rc;

#[derive(Debug)]
enum List {
    Cons(i32, Rc<RefCell<List>>),
    Nil,
}

use crate::List::{Cons, Nil};

fn main() {
    let list = Rc::new(RefCell::new(Cons(
        2,
        Rc::new(RefCell::new(Cons(1, Rc::new(RefCell::new(Nil))))),
    )));

    let a = Rc::new(Cons(3, Rc::clone(&list)));
    let b = Rc::new(Cons(4, Rc::clone(&list)));

    if let Cons(v, _) = &mut *list.borrow_mut() {
        *v = 9;
    }

    println!("{:?}", list);
    println!("{:?}", a);
    println!("{:?}", b);
}
