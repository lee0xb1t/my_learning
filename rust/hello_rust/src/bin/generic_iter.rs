#![allow(unused)]

fn main() {
    let mut v = vec![1, 2, 3, 4];

    // for mut x in v {
    //     x+=1;
    //     println!("x: {x}");
    // }

    for x in v.iter() {
        println!("x: {x}");
    }

    for x in v.iter_mut() {
        *x += 1;
        println!("x: {x}");
    }
}
