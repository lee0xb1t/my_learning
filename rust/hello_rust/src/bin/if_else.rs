fn main() {
    let x = -10;

    if x % 2 == 0 {
        println!("{x} is even");
    } else {
        println!("{x} is odd");
    }

    let z = if x > 0 {
        1
    } else if x < 0 {
        -1
    } else {
        x
    };

    println!("z: {z}");
}
