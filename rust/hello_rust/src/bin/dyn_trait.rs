#![allow(unused)]

struct Cat;
struct Dog;

trait Animal {
    fn speak(&self) -> String;
}

impl Animal for Cat {
    fn speak(&self) -> String {
        "miao".to_string()
    }
}

impl Animal for Dog {
    fn speak(&self) -> String {
        "wang".to_string()
    }
}

fn speak(a: &impl Animal) {
    println!("static speak: {}", a.speak());
}

fn return_concrete_type() -> impl Animal {
    Dog
}

fn dyn_speak(a: &dyn Animal) {
    println!("dyn speak: {}", a.speak());
}

fn return_dyn(rand: i32) -> Box<dyn Animal> {
    if rand < 10 {
        Box::new(Dog)
    } else {
        Box::new(Cat)
    }
}

fn dyn_speak1<T: AsRef<dyn Animal>>(animal: &T) {
    println!("dyn speak1: {}", animal.as_ref().speak());
}

fn dyn_speak2(animal: &impl AsRef<dyn Animal>) {
    println!("dyn speak1: {}", animal.as_ref().speak());
}

fn main() {
    let d = Dog;
    let c = Cat;

    speak(&d);
    speak(&c);

    println!("return type speak: {}", return_concrete_type().speak());

    let animal = "cat";
    let animal: &dyn Animal = match animal {
        "dog" => &Dog,
        _ => &Cat,
    };

    dyn_speak(animal);

    let a: Box<dyn Animal> = return_dyn(10);
    dyn_speak(&*a);
    dyn_speak(a.as_ref());
    a.speak();

    dyn_speak1(&a);
    dyn_speak2(&a);
}
