#![allow(unused)]

// struct Matrix<const M: usize, const N: usize> {  // compile error
//     data: [f64; M * N]
// }

#[derive(Debug)]
struct Matrix<const M: usize, const N: usize> {
    data: Vec<f64>,
}

impl<const M: usize, const N: usize> Matrix<M, N> {
    fn new() -> Self {
        Self {
            data: vec![0.0; M * N],
        }
    }
}

fn main() {
    let m: Matrix<2, 3> = Matrix::new();
    println!("{:?}", m);
}
