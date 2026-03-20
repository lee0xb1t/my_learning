#![allow(unused)]

use std::cmp::PartialOrd;

#[derive(Debug)]
struct Point<T = i32> {
    x: T,
    y: T,
}

fn swap<A, B>(t: (A, B)) -> (B, A) {
    (t.1, t.0)
}

fn find_max<T: PartialOrd>(s: &[T]) -> Option<&T> {
    if s.is_empty() {
        return None;
    }

    let mut max = &s[0];

    for v in s {
        if v > max {
            max = v;
        }
    }

    Some(max)
}

impl<T: std::default::Default> Point<T> {
    fn default() -> Self {
        Self {
            x: T::default(),
            y: T::default(),
        }
    }

    fn new(x: T, y: T) -> Self {
        Self { x: x, y: y }
    }

    fn move_to(&mut self, x: T, y: T) {
        self.x = x;
        self.y = y;
    }
}

fn main() {
    let p = Point {
        x: 1.0f32,
        y: 2.0f32,
    };
    let p = Point { x: 1, y: 2 };

    let t = (1, 2u32);
    let s = swap(t);
    println!("{:?}", s);

    let v = vec![1, 2, 3, 4, 1];
    let max = find_max(&v);
    println!("{:?}", max);

    let v = vec!['a', 'b', 'z', 'c', 'y'];
    let max = find_max(&v);
    println!("{:?}", max);

    let mut p = Point::new(1f32, 2.0);
    let mut p = Point::default();
    p.move_to(10.0, 20.0);
    println!("{:?}", p);
}
