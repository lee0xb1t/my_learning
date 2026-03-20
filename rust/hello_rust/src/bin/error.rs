#![allow(unused)]

#[derive(Debug)]
enum MathError {
    DivByZero,
    Other,
}

fn div(a: i32, b: i32) -> Result<i32, MathError> {
    if b == 0 {
        return Err(MathError::DivByZero);
    }
    Ok(a / b)
}

fn main() {
    let x = [1, 2, 3];
    let v = x.get(9);
    if let Some(x) = v {
        println!("x is {x}");
    } else {
        println!("v is none");
    }

    let a = 1;
    let b = 0;
    let c = div(a, b);
    match c {
        Ok(v) => println!("{a} / {b} = {v}"),
        Err(e) => println!("{a} / {b} => {:?}", e),
    }
}
