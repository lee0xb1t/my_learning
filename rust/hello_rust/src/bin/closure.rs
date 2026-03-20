#![allow(unused)]

fn f_fn() -> impl Fn(i32) -> i32 {
    let v = 1;
    move |x| x + v
}

fn f_fn_mut() -> impl FnMut() {
    let mut s = "Hello".to_string();
    move || {
        s += " Rust";
        println!("{s}");
    }
}

fn f_fn_once() -> impl FnOnce() -> String {
    let mut s = "Hello".to_string();
    move || {
        s += " Rust";
        s
    }
}

fn main() {
    let f = |x| x + 2;
    f(1);
    // f(1.0); // compile error

    let v = 1;
    let f = move |x| x + v;
    f(1);

    let s = "Hello".to_string();
    let p = || {
        println!("closure {s}");
    };
    p();
    p();
    println!("{s}");

    let mut s = "Hello".to_string();
    let mut p = || {
        s += " Rust";
    };
    p();
    p();
    println!("{s}");

    let s = "Hello".to_string();
    let p = move || {
        println!("once {s}");
        s
    };
    p();
    // p(); // compile error

    //
    let f = f_fn();
    f(1);
    f(2);

    let mut f_mut = f_fn_mut();
    f_mut();
    f_mut();

    let s = f_fn_once();
    println!("{}", s());
}
