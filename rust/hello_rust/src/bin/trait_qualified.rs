#![allow(unused)]

trait Color {
    fn get(&self) -> &String;
}

trait Rectangle {
    fn get(&self) -> (i32, i32, i32, i32);
}

struct Square {
    color: String,
    x: i32,
    y: i32,
    size: i32,
}

impl Color for Square {
    fn get(&self) -> &String {
        &self.color
    }
}

impl Rectangle for Square {
    fn get(&self) -> (i32, i32, i32, i32) {
        (self.x, self.y, self.size, self.size)
    }
}

fn main() {
    let s = Square {
        color: "red".to_string(),
        x: 0,
        y: 0,
        size: 10,
    };

    s.color.clone();
    let color = Color::get(&s);
    let (x, y, width, height) = Rectangle::get(&s);
    println!("color: {}", color);
    println!("x: {x}, y: {y}, width: {width}, height: {height}");
}
