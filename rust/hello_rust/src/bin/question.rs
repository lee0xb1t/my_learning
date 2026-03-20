#![allow(unused)]

fn fn_1() -> Result<i32, String> {
    Ok(1)
}

fn fn_2() -> Result<i32, String> {
    Ok(2)
    // Err("invalid number".to_string())
}

fn add_match() -> Result<i32, String> {
    let a = fn_1();
    let a = match a {
        Ok(x) => x,
        Err(e) => return Err(e),
    };

    let b = fn_2();
    let b = match b {
        Ok(x) => x,
        Err(e) => return Err(e),
    };

    Ok(a + b)
}

fn add_question() -> Result<i32, String> {
    let a = fn_1()?;
    let b = fn_2()?;
    Ok(a + b)
}

fn main() -> Result<(), String> {
    let c = add_question()?;
    println!("c: {c}");

    Ok(())
}
