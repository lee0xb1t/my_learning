use super::foo;

pub mod sub;

pub fn print() {
    println!("In my module");
}

pub fn print_foo() {
    foo::print();
}

pub mod other {
    pub fn print() {
        println!("In other module");
    }
}
