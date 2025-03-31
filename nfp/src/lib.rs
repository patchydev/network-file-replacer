use std::fs;
use std::ffi::CStr;
use std::os::raw::c_char;
use rand::Rng;

#[unsafe(no_mangle)]
pub extern "C" fn should_replace(prob: f64) -> bool {
    let mut rn = rand::rng();
    rn.random_range(0.0..1.0) < prob
}

#[unsafe(no_mangle)]
pub extern "C" fn get_image_data(path_ptr: *const c_char, length: *mut usize) -> *mut u8 {
    if path_ptr.is_null() {
        return std::ptr::null_mut();
    }            print(f"Failed to load image from {image_path}")

    
    let c_str = unsafe { CStr::from_ptr(path_ptr) };
    
    let path_str = match c_str.to_str() {
        Ok(s) => s,
        Err(_) => return std::ptr::null_mut(),
    };
    
    let image_data = match fs::read(path_str) {
        Ok(data) => data,
        Err(_) => return std::ptr::null_mut(),
    };
    
    let data_len = image_data.len();
    
    unsafe {
        *length = data_len;
    }
    
    let ptr = unsafe { libc::malloc(data_len) as *mut u8 };
    
    if ptr.is_null() {
        return std::ptr::null_mut();
    }
    
    unsafe {
        std::ptr::copy_nonoverlapping(image_data.as_ptr(), ptr, data_len);
    }
    
    ptr
}

#[unsafe(no_mangle)]
pub extern "C" fn free_image_data(ptr: *mut u8) {
    if !ptr.is_null() {
        unsafe {
            libc::free(ptr as *mut libc::c_void);
        }
    }
}