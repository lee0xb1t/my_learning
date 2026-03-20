use super::other;

#[derive(Debug)]
pub struct S {
    pub name: String,
    pub age: i32,
}

pub fn print() {
    println!("In my::sub module");
}

pub fn print_other() {
    other::print();
}
