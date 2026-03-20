#![allow(unused)]

use hello_rust::my;

fn main() {
    my::print();
    my::sub::print();

    let s = my::sub::S {
        name: "Lee".to_string(),
        age: 100,
    };
    println!("s: {:?}", s);

    my::sub::print_other();
    my::print_foo();
}
