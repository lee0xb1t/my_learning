#![allow(unused)]

fn main() {
    let x: Option<i32> = Some(1);
    // let x: Option<i32> = None;
    match x {
        Some(v) => println!("match Some {v}"),
        _ => {}
    }

    // if let
    if let Some(v) = x {
        println!("if let {v}");
    }

    // let else
    let Some(v) = x else {
        // diverge
        panic!("x is none");
    };
    println!("let else {v}")
}
