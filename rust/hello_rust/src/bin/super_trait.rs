#![allow(unused)]

struct Rust;

trait Compiler {
    fn compile(&self, file_path: &str) -> String;
}

trait Language {
    fn name(&self) -> String;
}

trait CompileLanguage: Compiler + Language {
    fn exec(&self, file_path: &str) {
        println!("name: {}", self.name());
        println!("cmd: {}", self.compile(file_path));
    }
}

impl Compiler for Rust {
    fn compile(&self, file_path: &str) -> String {
        format!("rustc {}", file_path)
    }
}

impl Language for Rust {
    fn name(&self) -> String {
        format!("Rust")
    }
}

impl CompileLanguage for Rust {}

fn main() {
    let r = Rust;
    r.exec("source.rs");
}
