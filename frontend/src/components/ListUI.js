import React, { useEffect, useState } from 'react';

const ListUI = () => {
  const [faces, setFaces] = useState([]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8765');

    ws.onopen = () => {
      console.log('WebSocket connection established');
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'face_detection') {
        setFaces(prevFaces => [...prevFaces, {
          id: faces.length + 1,
          face_id: message.face_id,
          timestamp: new Date(message.timestamp * 1000).toLocaleString()
        }]);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
    };

    return () => {
      ws.close();
    };
  }, []);

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Face ID</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {faces.map(face => (
            <tr key={face.id}>
              <td>{face.id}</td>
              <td>{face.face_id}</td>
              <td>{face.timestamp}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ListUI;
