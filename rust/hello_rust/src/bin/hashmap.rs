#![allow(unused)]

use std::collections::HashMap;

fn main() {
    let mut m: HashMap<&str, i32> = HashMap::new();

    m.insert("green", 100);
    m.insert("red", 120);

    let score = m.get("green");
    match score {
        Some(val) => println!("green team score: {val}"),
        None => {}
    }

    m.entry("yellow").or_insert(10);

    for v in m.iter() {
        println!("team: {}, score: {}", v.0, v.1);
    }
}
