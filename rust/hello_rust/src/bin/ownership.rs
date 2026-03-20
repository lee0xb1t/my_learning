#![allow(unused)]

fn take(s: String) {
    println!("{s}");
}

fn main() {
    // 每个值都有所有者
    let s = String::from("Hello Rust");

    // 一次只能有一个所有者
    let s1 = s;
    // println!("s: {s}");
    println!("s1: {s1}");

    // 离开作用域后，值被丢弃
    let s = String::from("aaa");
    {
        let a = s;
    }
    // "aaa" value is dropped after go out the scope
    // println!("{s}"); // error

    // function with move ownership
    let s = String::from("value");
    take(s);
    // println!("{s}"); //error
}
