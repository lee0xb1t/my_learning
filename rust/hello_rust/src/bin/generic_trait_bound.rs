#![allow(unused)]

trait A {}
trait B {}
trait C {}

impl A for i32 {}
impl B for i32 {}
impl C for i32 {}
impl A for u32 {}

fn w<T: A>(x: T) {}

fn m<T: A + B, Y: B + C>(x: T, y: Y) {}

fn n<T: A + B, Y: B + C>(x: T, y: Y)
where
    T: A + B,
    Y: B + C,
{
}

// impl语法和trait bound语法不同

// x和y可以是不同类型
fn a(x: impl A, y: impl A) {}
fn c<T: A, U: A>(x: T, y: U) {}

// x和y必须是相同类型
fn b<T: A>(x: T, y: T) {}

fn main() {
    let i = 1i32;
    let u = 1u32;
    let f = 1.0f32;

    w(i);
    w(u);

    m(i, i);
    // m(i, u);    // compile error

    n(i, i);
}
