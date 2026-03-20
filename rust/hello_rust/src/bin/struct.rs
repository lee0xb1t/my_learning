#![allow(unused)]

use std::ops::RangeBounds;

#[derive(Debug)]
struct Point {
    x: f32,
    y: f32,
}

struct Point3D(f32, f32, f32);

#[derive(Debug)]
struct Empty;

#[derive(Debug)]
struct Circle {
    center: Point,
    radius: f32,
}

fn main() {
    // create
    let p = Point { x: 1.1, y: 2.2 };
    println!("point.x = {}, point.y = {}", p.x, p.y);

    let empty = Empty;
    println!("{:?}", empty);

    // debug
    let circle = Circle {
        center: p,
        radius: 4.0,
    };
    println!("{:?}", circle);

    // shortcut
    let x = 10.0f32;
    let y = 44.33f32;

    let p = Point { x, y };
    println!("{:?}", p);

    // copy fileds
    let p0 = Point { x: 1.0, y: 2.0 };
    println!("p0: {:?}", p0);
    let p1 = Point { x: 999.0, ..p0 };
    println!("p1: {:?}", p1);

    // modify
    let mut p = Point { x: 100.0, y: 0.0 };
    println!("before modify: {:?}", p);
    p.x = 0.0;
    p.y += 10.0;
    println!("after modify: {:?}", p);
}
