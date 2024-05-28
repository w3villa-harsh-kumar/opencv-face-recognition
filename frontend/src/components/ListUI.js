import React from "react";



const ListUI = () => {


  return (
    <div className="table-container">


      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Check In</th>
            <th>Check Out</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>1</td>
            <td>John Doe</td>
            <td>2024-05-01 09:00:00</td>
            <td>2024-05-01 17:00:00</td>
          </tr>
          <tr>
            <td>2</td>
            <td>Jane Smith</td>
            <td>2024-05-02 09:15:00</td>
            <td>2024-05-02 16:45:00</td>
          </tr>
          <tr>
            <td>3</td>
            <td>Mike Johnson</td>
            <td>2024-05-03 08:45:00</td>
            <td>2024-05-03 17:15:00</td>
          </tr>
          <tr>
            <td>4</td>
            <td>Emily Davis</td>
            <td>2024-05-04 09:30:00</td>
            <td>2024-05-04 16:30:00</td>
          </tr>
        </tbody>
      </table>

    </div>

  );
};




export default ListUI;