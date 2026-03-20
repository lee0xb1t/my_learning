#![allow(unused)]
use std::collections::HashMap;

fn main() {
    let v = vec![1, 2, 3, 4, 5];
    let data: Vec<i32> = v.into_iter().filter(|x| *x != 4).map(|x| x * x).collect();
    println!("data: {:?}", data);

    let keys: Vec<String> = vec!["a", "b", "c", "d"]
        .into_iter()
        .map(|x| x.to_string())
        .collect();
    let vals = vec![1, 2, 3];
    let zipped: HashMap<String, i32> = keys.into_iter().zip(vals.into_iter()).collect();
    println!("zipped: {:?}", zipped);

    let vals = (1..=100).collect::<Vec<i32>>();
    let f = vals.iter().fold(0, |acc, x| acc + x);
    println!("f: {:?}", f);

    let (the, guardian, stands, resolute) = ("the", "Turbofish", "remains", "undefeated");
    let _: (bool, bool) = (the < guardian, stands > (resolute));
}
