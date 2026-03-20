#![allow(unused)]

#[derive(Debug)]
struct Point {
    x: f32,
    y: f32,
}

impl Point {
    // static method
    fn zero() -> Self {
        Self { x: 0.0, y: 0.0 }
    }

    // method
    fn move_to(&mut self, x: f32, y: f32) {
        self.x = x;
        self.y = y;
    }

    fn distance(&self) -> f32 {
        (self.x * self.x + self.y * self.y).sqrt()
    }
}

fn main() {
    let mut p = Point::zero();
    p.move_to((3.0f32).sqrt(), 1.0);
    println!("{:?}", p);
    let d = p.distance();
    println!("distance: {}", d);
}
