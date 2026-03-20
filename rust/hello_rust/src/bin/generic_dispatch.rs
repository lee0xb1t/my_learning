#![allow(unused)]

#[derive(Debug)]
struct A;

#[derive(Debug)]
struct B;

trait F {}
trait M {}

trait FM: F + M {}

impl F for A {}
impl M for A {}

// 为所有实现F+M的类型实现FM
impl<T: F + M> FM for T {}

impl F for B {}

fn static_dispatch<T: F>(o: &T) {}

fn dyn_dispatch(o: &dyn F) {}

// box会转移所有权
fn dyn_dispatch_box(o: Box<dyn F>) {}

fn main() {
    let a = A;
    let b = B;

    static_dispatch(&a);
    static_dispatch(&b);

    let input = "a";
    let obj: &dyn F = match input {
        "a" => &A,
        "b" => &B,
        _ => panic!(),
    };

    dyn_dispatch(obj);

    let input = "a";
    let obj: Box<dyn F> = match input {
        "a" => Box::new(A),
        "b" => Box::new(B),
        _ => panic!(),
    };

    dyn_dispatch_box(obj);
}
