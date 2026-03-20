#![allow(unused)]

#[derive(Debug)]
struct Tree {
    value: i32,
    left: Option<Box<Tree>>,
    right: Option<Box<Tree>>,
}

fn main() {
    let tree = Tree {
        value: 1,
        left: Some(Box::new(Tree {
            value: 2,
            left: None,
            right: Some(Box::new(Tree {
                value: 3,
                left: None,
                right: None,
            })),
        })),

        right: Some(Box::new(Tree {
            value: 4,
            left: None,
            right: None,
        })),
    };

    println!("tree: {:#?}", tree);

    println!(
        "tree.left.right.value = {}",
        tree.left.unwrap().right.unwrap().value
    );
}
