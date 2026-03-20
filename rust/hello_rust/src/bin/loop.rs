#![allow(unused)]

fn main() {
    // loop
    let mut i = 0;
    loop {
        if i == 3 {
            break;
        }
        println!("loop i: {i}");
        i += 1;
    }

    // while
    let mut i = 0;
    while i < 4 {
        println!("while i: {i}");
        i += 1;
    }

    //for loop
    for i in 0..=5 {
        println!("for loop i: {i}");
    }

    // for loop array
    let arr = [1, 2, 3, 4];
    for v in arr {
        println!("arr v: {v}");
    }

    // usize and range
    let sz = arr.len();
    for i in 0..sz {
        println!("arr[{i}]: {}", arr[i]);
    }

    // iter
    let vector = vec![1, 2, 3, 4];
    for v in vector.iter() {
        println!("vector v: {v}");
    }
    for v in vector.iter() {
        println!("vector v: {v}");
    }

    let mut i = 0;
    let z = loop {
        if i == 3 {
            break 999;
        }
        i += 1;
    };
    println!("loop return z: {z}");
    let z = for i in 0..4 {
        println!("for loop return empty tuple, {i}")
    };
    // println!("for loop z: {z}");

    // labels
    'outer: for i in 0..10 {
        'inner: for j in 0..8 {
            println!("loop labels {i}, {j}");
            if i == 4 && j == 5 {
                break 'outer;
            }
        }
    }
}
