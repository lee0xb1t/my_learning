#![allow(unused)]

use std::{fs::File, io::Read, num::ParseIntError};

#[derive(Debug)]
enum MathError {
    DivByZero,
}

#[derive(Debug)]
enum ParseError {
    InvalidNumber,
}

impl std::fmt::Display for MathError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "math error {:?}", self)
    }
}

impl std::fmt::Display for ParseError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "parse error {:?}", self)
    }
}

impl std::error::Error for MathError {}
impl std::error::Error for ParseError {}

fn f1() -> Result<i32, MathError> {
    Ok(1)
    // Err(MathError::DivByZero)
}

fn f2() -> Result<i32, ParseError> {
    Ok(2)
}

fn f3() -> Result<i32, Box<dyn std::error::Error>> {
    let a = f1()?;
    let b = f2()?;
    Ok(a + b)
}

fn read(path: &str) -> Result<Vec<String>, std::io::Error> {
    let mut f = File::open(path)?;
    let mut str = String::new();
    f.read_to_string(&mut str)?;
    let lines = str
        .trim()
        .split('\n')
        .map(|s| s.trim().to_string())
        .collect();
    Ok(lines)
}

fn sum(lines: Vec<String>) -> Result<i32, ParseIntError> {
    let mut sum = 0;
    for line in lines {
        let num: i32 = line.parse()?;
        sum += num;
    }
    Ok(sum)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let c = f3()?;
    println!("c: {c}");

    let lines = read("./data/box_dyn_error.txt")?;
    let sum = sum(lines)?;
    println!("sum: {sum}");

    Ok(())
}
