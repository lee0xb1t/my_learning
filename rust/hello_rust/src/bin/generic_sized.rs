#![allow(unused)]

fn f<T: Sized>(x: T) {}

fn q<T: ?Sized>(x: &T) -> &T {
    x
}

trait A {}

impl A for i32 {}

fn main() {
    let x = 1i32;
    f(x);
    // q(x); //compile error

    struct S {
        x: i32,
        y: i32,
    }

    let s = S { x: 0, y: 0 };
    f(s);
    // q(&s); //compile error

    let v = vec![1, 2, 31];
    f(&v[0..2]);
    q(&v[0..3]);

    let arr = [0; 5];
    f(&arr[0..2]);
    q(&arr[0..3]);

    let slice = &[0; 5];
    f(slice);
    q(slice);

    let s: &str = "hello";
    f(s);
    q(s);

    let d = Box::new(1i32);
    let d = q(&d);
}
