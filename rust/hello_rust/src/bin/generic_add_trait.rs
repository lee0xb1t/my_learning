#![allow(unused)]
use std::ops::Add;

#[derive(Debug)]
struct Point<T> {
    x: T,
    y: T,
}

impl<T: Add<Output = T>> Add for Point<T> {
    type Output = Point<T>;
    fn add(self, other: Self) -> Self::Output {
        Self {
            x: self.x + other.x,
            y: self.y + other.y,
        }
    }
}

fn main() {
    let p0 = Point { x: 1, y: 2 };
    let p1 = Point { x: 2, y: 3 };
    let p3 = p0 + p1;
    println!("p3: {:?}", p3);
}
