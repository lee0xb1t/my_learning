#![allow(unused)]
use std::rc::Rc;

// enum List<'a> {
//     Cons(i32, &'a Box<List<'a>>),
//     Nil
// }

enum List {
    Cons(i32, Rc<List>),
    Nil,
}

use crate::List::{Cons, Nil};

fn main() {
    // let nil = Box::new(Nil);
    // let l1 = Box::new(Cons(1, &nil));
    // let l2 = Box::new(Cons(2, &l1));
    // let a = Cons(3, &l2);
    // let b = Cons(4, &l2);

    let list = Rc::new(Cons(2, Rc::new(Cons(1, Rc::new(Nil)))));
    println!("ref count: {}", Rc::strong_count(&list));
    let a = Rc::new(Cons(3, Rc::clone(&list)));
    println!("ref count: {}", Rc::strong_count(&list));
    {
        let b = Rc::new(Cons(4, Rc::clone(&list)));
        println!("ref count: {}", Rc::strong_count(&list));
    }
    println!("dropped ref count: {}", Rc::strong_count(&list));

    /*a: Rc<List> */
    let mut cur: &List = &a;
    while let Cons(v, next) = cur {
        print!("{v} -> ");
        cur = next;
    }
    println!("Nil");
}
