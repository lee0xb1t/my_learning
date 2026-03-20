fn borrow(s: &[i32]) {
    println!("borrow {:?}", s);
}

fn borrow_mut(s: &mut [i32]) {
    s[0] = -1;
}

fn split_at(s: &[i32], i: usize) -> (&[i32], &[i32]) {
    (&s[0..i], &s[i..])
}

fn main() {
    let a: [i32; 5] = [1, 2, 3, 4, 5];
    borrow(&a[0..2]);

    // borrow mut
    let mut a = [1, 2, 3, 4, 5, 6, 7];
    println!("a before borrow mut: {:?}", a);
    borrow_mut(&mut a[1..4]);
    println!("a after borrow mut: {:?}", a);

    let a = [1, 2, 3, 4, 5, 6, 7, 8];
    let (s0, s1) = split_at(&a, 3);
    println!("s0: {:?}", s0);
    println!("s1: {:?}", s1);
    println!("a: {:?}", a);
}
