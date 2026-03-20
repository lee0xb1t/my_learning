#![allow(unused)]

enum Animal {
    Dog,
    Cat,
    Duck,
    Mouse,
}

fn main() {
    let x = 1;
    match x {
        1 => println!("one"),
        2 => println!("two"),
        3 => println!("three"),
        _ => println!("other"),
    }

    match x {
        1 | 2 | 3 => println!("one or two or three"),
        _ => println!("other"),
    }

    // range
    match x {
        1..=10 => println!("between 1 and 10"),
        _ => println!("other"),
    }

    // @
    match x {
        i @ 1..=10 => println!("between 1 and 10, this is {i}"),
        _ => println!("other"),
    }

    let animal = Animal::Cat;
    let animal_sound = match animal {
        Animal::Cat => "miaomiao",
        Animal::Dog => "wangwang",
        Animal::Duck => "gaga",
        _ => "?",
    };
    println!("animal sound: {animal_sound}");

    let x = Some(1);
    match x {
        Some(v) => println!("x is {v}"),
        None => println!("x is none"),
    }

    let x: Result<i32, String> = Err("div by 0".to_string());
    match x {
        Ok(v) => println!("Ok {v}"),
        Err(msg) => println!("Err '{msg}'"),
    }
}
