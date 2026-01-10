mod decoder;
mod strucs;
mod utils;

use decoder::bsii_decoder::decode;
use strucs::data_sii::SignatureType;
use utils::aes::decrypt;
use utils::file_type::try_read_u32;
use utils::zlib::uncompress;

// ==========================
// Core Rust API (UNCHANGED)
// ==========================
pub fn decrypt_bin_file(file_bin: &Vec<u8>) -> Result<Vec<u8>, String> {
    let file_type = match try_read_u32(file_bin) {
        Ok(res) => res,
        Err(e) => return Err(e),
    };

    if file_type == SignatureType::PlainText as u32 {
        return Ok(file_bin.clone());
    }

    if file_type == SignatureType::Encrypted as u32 {
        let mut data = match decrypt(file_bin) {
            Ok(res) => res,
            Err(_) => return Err("Error decrypting data".to_string()),
        };

        match uncompress(&data.data) {
            Ok(res) => data.data = res,
            Err(e) => return Err(e),
        };

        let file_type_verify = match try_read_u32(&data.data) {
            Ok(file_type) => file_type,
            Err(e) => return Err(e),
        };

        if file_type_verify == SignatureType::PlainText as u32 {
            return Ok(data.data);
        }

        decode(&data.data)
    } else if file_type == SignatureType::Binary as u32 {
        decode(file_bin)
    } else {
        Err("Invalid file type".to_string())
    }
}

// =====================================================
// PyO3 bindings (ONLY compiled with feature = "python")
// =====================================================
#[cfg(feature = "python")]
use pyo3::prelude::*;

#[cfg(feature = "python")]
#[pyfunction]
fn decrypt_sii_bytes(data: &[u8]) -> PyResult<Vec<u8>> {
    decrypt_bin_file(&data.to_vec())
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e))
}

#[cfg(feature = "python")]
#[pymodule]
fn decrypt_truck(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(decrypt_sii_bytes, m)?)?;
    Ok(())
}
