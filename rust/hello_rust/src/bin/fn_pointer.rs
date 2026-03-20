#![allow(unused)]

fn add(x: i32, y: i32) -> i32 {
    x + y
}

fn do_twice(add: fn(i32, i32) -> i32, x: i32, y: i32) -> i32 {
    add(x, y) + add(x, y)
}

fn main() {
    let f: fn(i32, i32) -> i32 = add;
    let f = add;
    let v = do_twice(f, 1, 2);
    println!("v: {v}");
}
