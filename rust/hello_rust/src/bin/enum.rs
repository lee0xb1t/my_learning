#![allow(unused)]

#[derive(Debug, PartialEq)]
enum Color {
    Red,
    Green,
    Blue,
    Rgba(u8, u8, u8, f32),
    Hex(String),
    Hsl { h: u8, s: u8, l: u8 },
}

fn main() {
    let color: Color = Color::Red;
    let color = Color::Green;
    let color = Color::Blue;
    let color = Color::Rgba(0, 0, 255, 0.5);
    let color = Color::Hex("#ffffff".to_string());
    let color = Color::Hsl { h: 1, s: 1, l: 200 };

    // Debug
    println!("{:?}", color);

    // PartialEq
    println!("{}", Color::Red == Color::Blue);
    println!("{}", Color::Red == Color::Red);
    println!("{}", Color::Rgba(0, 0, 1, 0.5) == Color::Rgba(0, 0, 2, 0.5));

    // Option
    let o = Some(Color::Hsl { h: 1, s: 2, l: 3 });
    println!("{:?}", o);
    let o: Option<i32> = None;
    println!("{:?}", o);

    // Result
    let r: Result<i32, String> = Ok(666);
    println!("{:?}", r);
    let r: Result<i32, String> = Err("div by 0".to_string());
    println!("{:?}", r);
}
