#![allow(unused)]

struct Solidity {
    version: String,
}

struct Vyper {
    version: String,
}

trait Compiler {
    fn compile(&self, file_path: &str) -> String;
}

impl Compiler for Solidity {
    fn compile(&self, file_path: &str) -> String {
        format!("compile {file_path} with version: {}", self.version)
    }
}

impl Compiler for Vyper {
    fn compile(&self, file_path: &str) -> String {
        format!("compile {file_path} with version: {}", self.version)
    }
}

fn compile(lang: &impl Compiler, file_path: &str) -> String {
    lang.compile(file_path)
}

fn main() {
    let sol = Solidity {
        version: "0.0.1".to_string(),
    };
    let vy = Vyper {
        version: "0.0.2".to_string(),
    };

    println!("{}", compile(&sol, "source.sol"));
    println!("{}", compile(&vy, "source.vy"));
}
