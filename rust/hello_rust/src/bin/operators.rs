#![allow(unused)]

fn main() {
    let a = 1;
    let b = 2;
    let c = a + b;
    let c = a - b;
    let c = a * b;
    let c = a / b;
    let c_f = a as f32 / b as f32;
    println!("{a} / {b} = {c}");
    println!("{} / {} = {}", a as f32, b as f32, c_f);

    // mod
    let a = -1;
    let b = 2;
    let c = a % b;
    println!("{a} % {b} = {c}");

    // boolean
    let a = true && false;
    println!("{a}");
    let a = false || true;
    println!("{a}");
    let a = !true;
    println!("{a}");

    // bitwise
    // 101
    let a = 5u8;
    // 011
    let b = 3u8;

    println!("a & b = {:03b}", a & b);
    println!("a | b = {:03b}", a | b);
    println!("a ^ b = {:03b}", a ^ b);
    println!("!a = {:03b}", !a);
    let c = 1u8 << 3;
    println!("1 << 3 = {:08b}", c);
    println!("1 << 3 = {}", c);

    println!("3 >> 1 = {}", 3u8 >> 1);
    println!("3 >> 1 = 0x{:02x}", 0x1eu8 >> 1);
}
