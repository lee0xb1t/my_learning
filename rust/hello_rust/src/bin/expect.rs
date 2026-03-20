#![allow(unused)]

fn main() {
    let x: Option<i32> = Some(1);
    let v = x.expect("x is none");
    println!("v: {v}");

    let x: Result<i32, String> = Err("div by 0".to_string());
    // let v = x.unwrap();
    let v = x.expect("math error");
    println!("v: {v}");
}
