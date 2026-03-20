#![allow(unused)]

fn main() {
    // create
    let v = vec![-1, 0, 1];
    let v = vec![1, 2, 3];
    let v = vec![1, 2, 3];
    let v: Vec<i32> = Vec::new();

    let v = vec![1u32, 2, 3];
    let v = vec![1u8; 5];

    println!("v = {:?}, len = {}", v, v.len());

    // get
    let v = vec![1, 2, 3];
    let x = v[0]; // 如果向量为空则恐慌
    let x = v.get(9); // 返回Option
    match x {
        Some(val) => println!("{val}"),
        None => println!("none"),
    }

    // update
    let mut v = vec![1, 2, 3];
    v[0] = 99;

    // push
    let mut v = vec![1, 2, 3];
    v.push(1);

    //pop
    let mut v = vec![1];
    let x = v.pop();
    let x = v.pop();
    match x {
        Some(val) => println!("{val}"),
        None => println!("none"),
    }

    //slice
    let v = vec![1, 2, 3];

    /*
    v47[0] = _$LT$alloc..vec..Vec$LT$T$C$A$GT$$u20$as$u20$core..ops..index..Index$LT$I$GT$$GT$::index::heb6e3755bb2db048(
             &v46, // slice ptr
             0i64,  // slice start
             (core::ops::range::Range<usize> *)2, // slice end
             (core::panic::location::Location *)&off_14001FA00);

    v47[0] = _$LT$alloc..vec..Vec$LT$T$C$A$GT$$u20$as$u20$core..ops..index..Index$LT$I$GT$$GT$::index::heb6e3755bb2db048(
            &v46,
            (alloc::vec::Vec<i32,alloc::alloc::Global> *)1,
            (core::ops::range::Range<usize> *)2,
            (core::panic::location::Location *)&off_14001FA00);
     */
    let s = &v[0..2];
    println!("vec slice: {:?}", s);

    v.is_empty();
    s.is_empty();

    // iterate
    let a = String::from("a");
    let b = String::from("b");
    let c = String::from("c");

    let mut v: Vec<String> = vec![];
    v.push(a);
    v.push(b);
    v.push(c);

    for x in &v {
        println!("{x}");
    }

    for x in v {
        println!("{x}");
    }
}
