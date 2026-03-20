#![allow(unused)]

use std::convert::From;

#[derive(Debug)]
struct Point<T> {
    x: T,
    y: T,
}

impl From<(i32, i32)> for Point<i32> {
    fn from(value: (i32, i32)) -> Self {
        Self {
            x: value.0,
            y: value.1,
        }
    }
}

fn main() {
    let t = (1, 2);
    let p = Point::from(t);
    let p: Point<i32> = t.into();
    println!("{:?}", p);
}
