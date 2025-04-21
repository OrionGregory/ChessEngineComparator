import React from "react";

function NavBar() {
  return (
    <nav style={styles.navbar}>
      <h2 style={styles.brand}>Chess Bot Arena</h2>
      <ul style={styles.navList}>
        <li style={styles.navItem}><a href="#" style={styles.navLink}>Play</a></li>
        <li style={styles.navItem}><a href="#" style={styles.navLink}>Upload</a></li>
        <li style={styles.navItem}><a href="#" style={styles.navLink}>Login</a></li>
        <li style={styles.navItem}><a href="#" style={styles.navLink}>Register</a></li>
      </ul>
    </nav>
  );
}

const styles = {
  navbar: {
    width: "100%",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "10px 10px",
    backgroundColor: "#333",
    color: "#fff",
  },
  brand: {
    margin: 0,
  },
  navList: {
    listStyle: "none",
    display: "flex",
    gap: "20px",
    margin: 0,
    padding: 0,
  },
  navItem: {
    display: "inline",
  },
  navLink: {
    color: "#fff",
    textDecoration: "none",
    fontSize: "16px",
  }
};

export default NavBar;
