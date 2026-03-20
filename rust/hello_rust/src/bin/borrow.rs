#![allow(unused)]

fn main() {
    // 借用规则
    // 1. 创建一个引用
    // 2. 不转移所有权

    // Immutable borrow
    let s = String::from("rust");
    let s1 = &s;
    println!("{}", *s1);
    println!("{} {s1}", s1);

    // Mutable borrow
    let mut s = String::from("Hello");
    let s1 = &mut s;

    // 同一时刻只能有一个可变借用
    // let s2 = &mut s; // error

    s1.push_str(" Rust");
    println!("{}", s);

    // s1使用完可以再次创建可变借用
    let s2 = &mut s;

    // 不能同时存在可变和不可变借用
    let s1 = &s;
    let s2 = &s;
    // let s3 = &mut s; //error
    println!("{s1}");

    // 引用的生命周期不能同时超过其所引用的值
    let s = String::from("test");
    let s1 = &s;
    // {
    //     // let s2 = s; // error
    // } // s2 is dropped
    // std::mem::drop(s);

    println!("{}", s1);

    // 函数的借用
    let s = String::from("Hello1");
    // take_ownership(s);
    // let s1 = take_ownership_return(s);
    borrow(&s);
}

fn take_ownership(s: String) {
    println!("take ownership {s}");
}

fn take_ownership_return(s: String) -> String {
    println!("take ownership return {s}");
    s
}

fn borrow(s: &str) {
    println!("borrow {s}");
}
